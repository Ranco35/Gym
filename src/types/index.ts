export enum UserRole {
  USER = "user",
  TRAINER = "trainer",
  ADMIN = "admin"
}

export interface Exercise {
  id: string;
  name: string;
  category: MuscleGroup;
  type: ExerciseType;
  description?: string;
  videoUrl?: string;
  imageUrl?: string;
}

export interface Set {
  weight: number;
  reps: number;
  rpe?: number;
  rir?: '+1' | '+2' | '+3';
  completed: boolean;
}

export interface WorkoutExercise {
  exerciseId: string;
  sets: Set[];
  notes?: string;
}

export interface Workout {
  id: string;
  date: string;
  exercises: WorkoutExercise[];
  metrics: {
    energyLevel: 'high' | 'medium' | 'low';
    sleepQuality: number;
    mood: 'great' | 'good' | 'neutral' | 'bad';
    pain?: {
      location: string;
      intensity: number;
    };
  };
}

export type MuscleGroup =
  | 'chest'
  | 'back'
  | 'legs'
  | 'shoulders'
  | 'arms'
  | 'core'
  | 'fullBody';

export type ExerciseType = 
  | 'strength'
  | 'hypertrophy'
  | 'endurance'
  | 'power'
  | 'mobility';