<?php

// database/factories/ContactFactory.php
$factory->define(Contact::class, function (Faker $faker) {
    return [
        'user_id' => User::factory(),
        'first_name' => $faker->firstName,
        'last_name' => $faker->lastName,
        'email' => $faker->unique()->safeEmail,
        'phone' => $faker->phoneNumber,
        'company' => $faker->company,
        'notes' => $faker->paragraph,
    ];
});