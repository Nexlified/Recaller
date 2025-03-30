<?php
 
use App\Models\Contact;
use function Livewire\Volt\{computed, state};
use Livewire\Volt\Component;
 
$count = computed(function () {
    return Contact::count();
});
 
state([
    'first_name' => '',
    'last_name' => '',
]);
$createContact = fn() => Contact::create([
    'user_id' => auth()->id(),
    'first_name' => $this->first_name,
    'last_name' => $this->last_name
]);
?>

<div>
    <form wire:submit="createContact" class="my-6 space-y-6">
<flux:input.group>
    <flux:input wire:model="first_name" :label="__('First Name')" type="text" required autofocus autocomplete="firstname" />
    <flux:input wire:model="last_name" :label="__('Last Name')" type="text" autofocus autocomplete="lastname" />
    <flux:button variant="primary" :label="__('Save')" type="submit" class="w-4">{{ __('Save') }}</flux:button>
</flux:input.group>
</form>
</div>
