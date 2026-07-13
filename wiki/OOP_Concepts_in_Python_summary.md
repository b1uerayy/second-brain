---
tags: [python, object-oriented-programming, abstract-classes, inheritance]
date_created: 2026-07-13
last_updated: 2026-07-13
source: OOP Concepts in Python.md
---

# OOP Concepts in Python

## Summary
The document provides a detailed explanation of Object-Oriented Programming (OOP) concepts using Python. It starts by defining an abstract class `Vehicle` that includes abstract methods `start`, `stop`, and instance methods `display`. The abstract methods are implemented by child classes `Car` and `Bike`, showcasing how inheritance works in OOP. Additionally, it covers the use of class and static methods.

## Key Concepts
- **Abstract Base Class (ABC)**: Used to create a base class with abstract methods.
- **@abstractmethod**: Decorator for defining abstract methods that must be implemented by child classes.
- **Instance Methods**: Methods using `self` to operate on an instance's data.
- **Class Methods**: Methods using `cls` and working on the class itself.
- **Static Methods**: Independent methods not dependent on any class or object state.

## Connections
[[Object-Oriented Programming]], [[Python Concepts]], [[Inheritance]], [[Abstract Base Classes]]

## Quotes Worth Keeping
- "Abstract → forces methods"
- "Instance → uses `self`"
- "Class → uses `cls`"
- "Static → no `self/cls"`