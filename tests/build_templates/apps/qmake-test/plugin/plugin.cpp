#include <QtQml>
#include <QtQml/QQmlContext>

#include "plugin.h"
#include "pluginname.h"

void PluginnamePlugin::registerTypes(const char *uri) {
    //@uri Pluginname
    qmlRegisterSingletonType<Pluginname>(uri, 1, 0, "Pluginname", [](QQmlEngine*, QJSEngine*) -> QObject* { return new Pluginname; });
}
