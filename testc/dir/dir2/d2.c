#include <stdlib.h>
#include <stdio.h>
void tt() {
  void *p = malloc(10), *p2 = malloc(20);
  fgetc(stdin);
  fgets(p, 10, stdin);

  free(p);
}
