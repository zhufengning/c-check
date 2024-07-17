#include <stdlib.h>
void tt() {
  void *p = malloc(10), *p2 = malloc(20);
  free(p);
}
