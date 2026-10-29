<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('cia_search_logs', function (Blueprint $table): void {
            $table->bigIncrements('id');
            $table->string('candidate_id', 191)->index();
            $table->json('request_payload');
            $table->json('results');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('cia_search_logs');
    }
};
