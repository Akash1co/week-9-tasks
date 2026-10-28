<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class LessonUser extends Model
{
    protected $table = 'lesson_user';

    protected $fillable = [
        'user_id',
        'lesson_id',
        'completed_at',
    ];
}
