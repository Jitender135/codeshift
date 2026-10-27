package com.codeshift.model;

import java.util.Objects;

/**
 * Pet model class representing a domestic animal entity.
 * Migrated to Python dataclass in CodeShift.
 */
public class Pet {
    private String id;
    private String name;
    private String species;
    private int age;

    public Pet() {
    }

    public Pet(String id, String name, String species, int age) {
        this.id = id;
        this.name = name;
        this.species = species;
        this.age = age;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSpecies() {
        return species;
    }

    public void setSpecies(String species) {
        this.species = species;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String speak() {
        if ("Dog".equalsIgnoreCase(species)) {
            return "Woof!";
        } else if ("Cat".equalsIgnoreCase(species)) {
            return "Meow!";
        }
        return "Hello!";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Pet pet = (Pet) o;
        return age == pet.age &&
                Objects.equals(id, pet.id) &&
                Objects.equals(name, pet.name) &&
                Objects.equals(species, pet.species);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, species, age);
    }

    @Override
    public String toString() {
        return "Pet{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", species='" + species + '\'' +
                ", age=" + age +
                '}';
    }
}
