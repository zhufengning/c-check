#include <stdio.h>
#include "lib.h"

unsigned x;

int f() {
  f();
  return 1;
}
int main() {
  int a = 0;
  x=a;
  printf("%d", a);
  f(a + 2);
  float fuc;
  sprintf("%lf scr", fuc );
  while (1) {
  }
}
