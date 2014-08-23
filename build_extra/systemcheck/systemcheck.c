/**
 ** This is a small test program for setting up some system related
 ** attributes
 **
 **/

#include <stdio.h>
#include <stdint.h>

int littleEndianCheck(void)
{
    union 
    {
        uint32_t i;
        char c[4];
    } bint = {0x01020304};

    return bint.c[0] == 4; 
}

int main()
{
  //checking the size of a long in bytes (needed by dtoa.c)
  printf("%zu\n", sizeof(long));
  //checking if it's little endian system (1) 
  printf("%d\n",littleEndianCheck());

  return 0;
}
