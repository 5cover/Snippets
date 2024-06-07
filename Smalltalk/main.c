m(s,t)
char *s;
char *t;
{
    int i;
    for (i=0; (*s++ = *t++) != '\0'; i++)
        ;
    return(i);
}

main()
{
    char str1[10];
    char str2[] = "Hello!";
    int len = m(str1, str2);
    int i;
    for (i=0; i<len; i++)
        putchar(str1[i]);
    exit(0);
}