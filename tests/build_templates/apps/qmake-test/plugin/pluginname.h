#ifndef PLUGINNAME_H
#define PLUGINNAME_H

#include <QObject>

class Pluginname: public QObject {
    Q_OBJECT

public:
    Pluginname();
    ~Pluginname() = default;

    Q_INVOKABLE void speak();
};

#endif
