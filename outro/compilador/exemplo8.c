#include <stdio.h>
#include <string.h>

// Funções de controle de dispositivos

void ligar(const char* id_device) {
    printf("%s ligado!\n", id_device);
}

void desligar(const char* id_device) {
    printf("%s desligado!\n", id_device);
}

void alerta(const char* id_device, const char* msg) {
    printf("%s recebeu o alerta:\n", id_device);
    printf("%s\n", msg);
}

void alerta_com_var(const char* id_device, const char* msg, int var) {
    printf("%s recebeu o alerta:\n", id_device);
    printf("%s %d\n", msg, var);
}

// Variáveis globais
int temperatura = 0;

int main() {
    // Código gerado do programa ObsAct
    alerta_com_var("Termometro", "Temperatura esta em", temperatura);
    
    return 0;
}
