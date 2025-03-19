package com.girihan;

public class Calculator {
    public int add(int a, int b) {

        if (a<0) {
            System.out.println("add: a is negative");
        }
        if (b<0) {
            System.out.println("add: b is negative");
        }
        return a + b;
    }
    public int subtract(int a, int b) {
        return a - b;
    }
    public int multiply(int a, int b) {
        return a * b;
    }
    public int divide(int a, int b) {
        return a / b;
    }
}
