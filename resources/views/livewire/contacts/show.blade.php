<?php

use Livewire\Volt\Component;
use App\Models\Contact;
use Illuminate\Support\Facades\Auth;

new class extends Component {
    public string $first_name;
    public string $last_name;
    public string $email;
    public string $gender;

    public function createContact(): void {
        $user = Auth::user();
        Contact::create([
        'user_id' => auth()->id(),
        'first_name' => $this->first_name,
        'last_name' => $this->last_name,
        'email' => $this->email
    ]);

    
    $this->dispatch('contact-created');
    $this->reset();
    }
}; ?>

<div class="flex flex-col items-start">
    @include('partials.contacts-heading')

<form wire:submit="createContact" class="my-6 space-y-6">
    <flux:input.group>
    <flux:input size="lg" wire:model="first_name" :label="__('First Name')" type="text" required autofocus autocomplete="firstname" />
    <flux:input wire:model="last_name" :label="__('Last Name')" type="text" autofocus autocomplete="lastname" />
</flux:input.group>
    <flux:input icon="mail" wire:model="email" :label="__('Email')" type="email" required autocomplete="email" />
    <flux:radio.group wire:model="gender" label="Gender" variant="segmented">
    <flux:radio icon="mars" label="Male" />
    <flux:radio icon="venus" label="Female" />
    <flux:radio icon="shield" label="Not Specified" />
</flux:radio.group>
    <div class="flex items-center gap-4">
        <div class="flex items-center justify-end">
            <flux:button variant="primary" type="submit" class="w-full">{{ __('Save') }}</flux:button>
        </div>

        <x-action-message class="me-3" on="profile-updated">
            {{ __('Saved.') }}
        </x-action-message>
    </div>
</form>
</div>