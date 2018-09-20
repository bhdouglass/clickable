TEMPLATE = aux
TARGET = qmake-test

QML_FILES += $$files(*.qml,true) \
             $$files(*.js,true)

CONF_FILES +=  ../qmake-test.apparmor \
               ../qmake-test.desktop

OTHER_FILES += $${CONF_FILES} \
               $${QML_FILES} \
               $${AP_TEST_FILES}

qml_files.path = /qmake-test
qml_files.files += $${QML_FILES}

config_files.path = /qmake-test
config_files.files += $${CONF_FILES}

INSTALLS+=config_files qml_files
