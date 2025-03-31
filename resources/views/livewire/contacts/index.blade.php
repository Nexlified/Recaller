<?php
use Livewire\WithPagination;
use Livewire\Volt\Component;
use App\Models\Contact;
use Illuminate\Support\Facades\Auth;

new class extends Component {
    public $sortBy = 'created_at';
    public $sortDirection = 'desc';

    public function sort($column) {
        if ($this->sortBy === $column) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortBy = $column;
            $this->sortDirection = 'asc';
        }
    }

    #[\Livewire\Attributes\Computed]
    public function contacts()
    {
        return \App\Models\Contact::query()
            ->tap(fn ($query) => $this->sortBy ? $query->orderBy($this->sortBy, $this->sortDirection) : $query)
            ->paginate(5);
    }

    public function deleteContact($contact): void
    {
        Contact::find($contact)->delete();
    }
}
?>
<div>
    <flux:button href="{{ route('contacts.create') }}" variant="primary" class="mb-4">{{ __('Create') }}</flux:button>


    <livewire:contacts.quick-create />
    <table class="mt-5 table-auto w-full border-collapse">
        <thead class="text-left">
            <tr>
                <th>
                    <button wire:click="sort('first_name')">First Name</button>
                </th>
                <th>
                    <button wire:click="sort('last_name')">Last Name</button>
                </th>
                <th class="hidden sm:table-cell">
                    <button wire:click="sort('email')">Email</button>
                </th>
                <th>
                    Actions
                </th>
            </tr>
        </thead>
        <tbody>

    @foreach ($this->contacts() as $contact)
            <tr>
                <td class="px-3 border m-1 border-accent-content">{{ $contact->first_name }}</td>
                <td class="px-3 border m-1 border-accent-content">{{ $contact->last_name }}</td>
                <td class="hidden sm:table-cell px-3 border m-1 border-accent-content">
                    {{ $contact->email }}
                </td>
                <td class="px-3 border m-1 border-accent-content">
                <flux:button.group>
                    <flux:button size="xs" variant="primary" icon="user-pen" href="{{ route('contacts.edit', $contact) }}" class="mb-4 mt-4"></flux:button>
                    <flux:button size="xs" href="{{ route('contacts.show', $contact) }}" variant="primary" class="mb-4 mt-4">{{ __('Show') }}</flux:button>
                    <flux:button size="xs" variant="danger" icon="user-x" wire:click="deleteContact({{ $contact->id }})" class="mb-4 mt-4"></flux:button>
                </flux:button.group>
            </td>
            </tr>

            @endforeach
        </tbody>
    </table>
</div>
