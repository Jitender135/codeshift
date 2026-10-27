package com.codeshift.repository;

import com.codeshift.model.Pet;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class PetRepository {
    private final List<Pet> pets = new ArrayList<>();

    public Pet save(Pet pet) {
        pets.add(pet);
        return pet;
    }

    public List<Pet> findAll() {
        return new ArrayList<>(pets);
    }

    public Optional<Pet> findById(String id) {
        return pets.stream()
                .filter(p -> p.getId() != null && p.getId().equals(id))
                .findFirst();
    }
}
