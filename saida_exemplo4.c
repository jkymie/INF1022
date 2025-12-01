#include <stdio.h>

// protótipos das funções ObsAct → C
void ligar(const char* dev);
void desligar(const char* dev);
void alerta(const char* dev, const char* msg);
void alerta_var(const char* dev, const char* msg, int var);

int main() {
    int umidade = 0;

    if (umidade < 40) { alerta("Monitor", "Ar seco detectado"); }

    return 0;
}

// implementações das funções
void ligar(const char* dev) { printf("%s ligado !\n", dev); }
void desligar(const char* dev) { printf("%s desligado !\n", dev); }
void alerta(const char* dev, const char* msg) {
    printf("%s recebeu o alerta :\n", dev);
    printf("%s\n", msg);
}
void alerta_var(const char* dev, const char* msg, int var) {
    printf("%s recebeu o alerta :\n", dev);
    printf("%s %d\n", msg, var);
}