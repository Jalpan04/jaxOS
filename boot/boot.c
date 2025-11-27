/*
 * jaxOS Bootloader (boot.c)
 * -------------------------
 * Simulates a BIOS/UEFI boot sequence before handing control
 * to the Neural Kernel (Python Runtime).
 */

#include <stdio.h>
#include <stdlib.h>
#include <windows.h> // For Sleep() on Windows

void clear_screen() { system("cls"); }

void sleep_ms(int milliseconds) { Sleep(milliseconds); }

int main() {
  clear_screen();

  printf("PHOENIX BIOS v4.0 Release 6.0\n");
  printf("Copyright 1985-2025 Phoenix Technologies Ltd.\n");
  printf("All Rights Reserved\n\n");

  sleep_ms(500);

  printf("CPU     : Neural Quantum Core @ 128 THz\n");
  sleep_ms(200);

  printf("Memory  : 64 KB OK\n");
  sleep_ms(300);

  printf("Primary Master : VECTOR_DB_DRIVE_01\n");
  sleep_ms(200);
  printf("Primary Slave  : CORTEX_MODEL_G3_12B\n");
  sleep_ms(500);

  printf("\nVerifying DMI Pool Data .");
  sleep_ms(200);
  printf(".");
  sleep_ms(200);
  printf(".");
  sleep_ms(500);
  printf(" Update Success\n");

  printf("\nBooting from Local Disk...\n");
  sleep_ms(1000);

  printf("Loading Kernel...");
  sleep_ms(800);

  // Handover to Python Kernel
  // We use system() to call the python interpreter
  int result = system("python kernel/main.py");

  if (result != 0) {
    printf("\n[!] Kernel Panic: Exit Code %d\n", result);
    printf("System Halted.\n");
    while (1)
      ;
  }

  return 0;
}
