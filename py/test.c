int f() {
  f();
  return 1;
}
int main() {
  int a = 0;
  printf("%d", a);
  f();
  while (1) {
  }
}
