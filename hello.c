#include <stdio.h>

// Function to return a hello world message
const char* hello_world_c() {
    return "Hello, World from C!";
}

// Main function to print the hello world message
int main() {
    printf("%s\n", hello_world_c());
    return 0;
}
