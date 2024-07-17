#include "dir/dir2/d2.h"
void lib_fun() {
  int x;
  x = x+1;
}

int foo() {
    int x = 1;
    int y = x + 2;
    return y;
}

int bar() {
    int x = 3;
    int y = x + 4;
    return y;
}

int hhh() {
    int a = foo();
    int b = bar();
    int x = a + b;
}
