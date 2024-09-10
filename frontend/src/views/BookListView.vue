<script setup lang="ts">
import { ref } from 'vue'

interface Book {
    unique_id: string
    title: string
    author: string
    isbn?: string
    cover_art?: string
    category?: string
}

const books = ref(Array<Book>())
fetch("http://localhost:8081/api/v1/books/list")
    .then(response => response.json())
    .then(data => { books.value = data.result })
    .then(() => console.log(`Number of Books ${books.value.length}`))
</script>

<template>
    <h1>Books List</h1>
    <div v-if="books">
        <div class="row row-cols-1 row-cols-md-3 g-4">
        <div v-for="book in books" :key="book.unique_id" class="col">
        <div class="card h-200" style="width: 18rem;">
            <img :src="book.cover_art" class="card-img-top"/>
            <div class="card-body">
                <h5 class="card-title">{{ book.title }}</h5>
                <p class="card-text">{{ book.author }}</p>
                <p class="card-text">{{ book.isbn }}</p>
            </div>
        </div>
        </div>
        </div>
    </div>
</template>