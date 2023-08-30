/opt/salt/scripts:
  file.directory:
    - user: root
    - group: root
    - mode: 755

/opt/salt/scripts/criteo_fdbshow:
  file.managed:
    - source:
      - salt://states/utilities/{{ grains["sonic_build_version"][:6] }}/criteo_fdbshow
    - mode: 755

/opt/salt/scripts/criteo_intf_information:
  file.managed:
    - source:
      - salt://states/utilities/{{ grains["sonic_build_version"][:6] }}/criteo_intf_information
    - mode: 755
