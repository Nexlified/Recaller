<?php

namespace App\Livewire\Forms;

use App\Models\Contact;
use Livewire\Attributes\Validate;
use Livewire\Form;

class QuickContactForm extends Form
{
    #[Validate('required|min:1')]
    public $first_name = '';

    public $last_name = '';

    public function store()
    {
        $this->validate();

        Contact::create($this->all());
    }
}
