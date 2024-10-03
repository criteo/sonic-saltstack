"""SONiC state module.

It aims to contain all the needed states function to manage the entire configuration of SONiC.

There are four main parts in SONiC configuration:

- bgp
- config_db
- snmp
- acl

Except for BGP, a change can cause to a service unavailability (docker containers need to be
rebooted when config is changed)
"""

from salt.exceptions import CommandExecutionError

__virtualname__ = "sonic"


def __virtual__():
    return __salt__["grains.get"]("nos") == "sonic"


def _bgp(template, context, saltenv, **_):
    return __salt__["sonic.bgp_config"](
        template_name=template,
        context=context,
        saltenv=saltenv,
        test=__opts__["test"],
    )


def _config_db(template, context, saltenv, reload_conf):
    return __salt__["sonic.configdb_config"](
        template_name=template,
        context=context,
        saltenv=saltenv,
        reload_conf=reload_conf,
        test=__opts__["test"],
    )


def _snmp(template, context, saltenv, **_):
    return __salt__["sonic.snmp_config"](
        template_name=template,
        context=context,
        saltenv=saltenv,
        test=__opts__["test"],
    )


def managed(name, templates, context=None, saltenv="base", reload_conf=False):
    """Manage full configuration.

    :param name: title of the action
    :param templates: dict of Jinja templates, supported keys: bgp, config_db, snmp
    :param context: variables to map with the templates
    :param saltenv: Salt environment
    """
    section_function = {"bgp": _bgp, "config_db": _config_db, "snmp": _snmp}
    ret = {"name": name, "result": True, "changes": {}, "comment": None}
    comments = {}

    for section, template in templates.items():
        if section not in section_function:
            comments[section] = "unsupported"
            continue

        result = section_function[section](
            template=template, context=context, saltenv=saltenv, reload_conf=reload_conf
        )

        comments[section] = result["comment"]
        ret["changes"][section] = result["changes"]
        if result["result"] is not None:
            ret["result"] &= result["result"]

    if ret["result"] and __opts__["test"]:
        ret["result"] = None

    ret["comment"] = ["** {} **\n{}".format(a, b) for a, b in comments.items()]

    return ret


def add_user(name, password, public_keys, groups, gid=None, clear_password=True):  # noqa: R0917
    """Add user.

    To avoid issues, users must have at least a password or a ssh key.

    :param name: username
    :param password: password
    :param public_keys: list of ssh public keys
    :param groups: list of groups of the user
    :param gid: default group id of the user, default: next available gid will be assigned
    :param clear_password: default True. If False: use hash with `openssl passwd -1`.
    """
    ret = {"name": name, "result": True, "changes": {}, "comment": None}
    changes = []
    comments = []

    # ensure at least a password or a ssh key is provided
    if not password and not public_keys:
        msg = "User '{}' must have either a password or a ssh key".format(name)
        raise CommandExecutionError(msg)

    remove_groups = True

    # security for admin user
    if name == "admin":
        gid = None
        remove_groups = False

    # user creation
    user_created = __states__["user.present"](
        name=name,
        groups=groups,
        gid=gid,
        password=password,
        hash_password=clear_password,
        createhome=True,
        shell="/bin/bash",
        remove_groups=remove_groups,
    )

    if not user_created["result"]:
        return user_created

    if user_created["changes"]:
        changes.append(user_created["changes"])

    if user_created["comment"]:
        comments.append(user_created["comment"])

    # ensure wanted ssh keys only are authorized
    keys_added = __states__["ssh_auth.manage"](name="sshkeys", user=name, ssh_keys=public_keys)

    # we keep ssh key comment only if there was issues to avoid too long result
    if not keys_added["result"]:
        comments.append({"sshkeys": keys_added["comment"]})

    if keys_added["changes"]:
        changes.append({"sshkeys": keys_added["changes"]})

    ret["result"] = keys_added["result"]
    ret["changes"] = changes
    ret["comment"] = comments

    return ret


def remove_user(name):
    """Remove user.

    :param name: username
    """
    return __states__["user.absent"](name=name, purge=True, force=True)
