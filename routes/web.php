<?php

use Illuminate\Support\Facades\Route;
use Livewire\Volt\Volt;

Route::get('/', function () {
    return view('welcome');
})->name('home');

Route::view('dashboard', 'dashboard')
    ->middleware(['auth', 'verified'])
    ->name('dashboard');

Route::middleware(['auth'])->group(function () {
    Route::redirect('settings', 'settings/profile');

    Volt::route('settings/profile', 'settings.profile')->name('settings.profile');
    Volt::route('settings/password', 'settings.password')->name('settings.password');
    Volt::route('settings/appearance', 'settings.appearance')->name('settings.appearance');

    Volt::route('contacts', 'contacts.index')->name('contacts.index');
    Volt::route('contacts/create', 'contacts.create')->name('contacts.create');
    Volt::route('contacts/{contact}/edit', 'contacts.edit')->name('contacts.edit');
    Volt::route('contacts/{contact}/delete', 'contacts.delete')->name('contacts.delete');
    Volt::route('contacts/{contact}/show', 'contacts.show')->name('contacts.show');

    Volt::route('journal', 'journal.index')->name('journal.index');
});

require __DIR__.'/auth.php';
