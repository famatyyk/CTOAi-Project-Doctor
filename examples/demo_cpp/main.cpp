#include <cstdio>
#include <cstring>

int main() {
    char* buf = new char[256];          // surowe new
    strcpy(buf, "hello");               // niebezpieczna funkcja
    printf("val=%d\n", 42);            // printf family
    int* p = (int*)buf;                 // C-style cast
    goto cleanup;                        // goto
    cleanup:
    return 0;
}
