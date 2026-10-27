package com.codeshift.service;

import com.codeshift.model.Pet;
import com.codeshift.repository.PetRepository;
import java.util.List;
import java.util.Optional;

public class PetService {
    private final PetRepository repository;

    public PetService(PetRepository repository) {
        this.repository = repository;
    }

    public Pet createPet(Pet pet) {
        return repository.save(pet);
    }

    public List<Pet> getAllPets() {
        return repository.findAll();
    }

    public Optional<Pet> getPetById(String id) {
        return repository.findById(id);
    }
}
