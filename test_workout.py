from workout_generator import save_workout

workout_description = """Z1-Z2 base with focus on efforts as follows:

-12' Z3 with 15" surge every 3'
-4' Z6 (near max)
-2x10' done as...
30" max / 30" Z2-Z3"""

filepath = save_workout("Mixed_Intervals", workout_description)
print(f"Workout saved to: {filepath}") 