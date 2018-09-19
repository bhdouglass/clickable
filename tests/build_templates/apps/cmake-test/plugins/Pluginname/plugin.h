#ifndef PLUGINNAMEPLUGIN_H
#define PLUGINNAMEPLUGIN_H

#include <QQmlExtensionPlugin>

class PluginnamePlugin : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QQmlExtensionInterface")

public:
    void registerTypes(const char *uri);
};

#endif
