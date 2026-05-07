export interface Ingredient {
  quantity: string | null;
  unit: string | null;
  item: string;
}

export interface Instruction {
  step_number: number;
  instruction_text: string;
}

export interface Nutrition {
  calories: string | null;
  protein: string | null;
  carbs: string | null;
  fat: string | null;
}

export interface Substitution {
  original: string;
  replacement: string;
  reason: string | null;
}

export interface ShoppingListItem {
  category: string;
  item: string;
}

export interface RelatedRecipe {
  title: string;
  description: string | null;
  suggested_url: string | null;
}

export interface RecipeDetail {
  id: number;
  url: string;
  title: string | null;
  cuisine: string | null;
  difficulty: string | null;
  prep_time: string | null;
  cook_time: string | null;
  total_time: string | null;
  servings: string | null;
  created_at: string;
  ingredients: Ingredient[];
  instructions: Instruction[];
  nutrition: Nutrition | null;
  substitutions: Substitution[];
  shopping_list: ShoppingListItem[];
  related_recipes: RelatedRecipe[];
}

export interface RecipeListItem {
  id: number;
  url: string;
  title: string | null;
  cuisine: string | null;
  difficulty: string | null;
  created_at: string;
}

export interface ExtractResponse {
  success: boolean;
  message: string;
  recipe: RecipeDetail | null;
  cached: boolean;
}

export interface HistoryResponse {
  success: boolean;
  recipes: RecipeListItem[];
  total: number;
}

export interface MealPlanResponse {
  success: boolean;
  recipe_titles: string[];
  combined_shopping_list: Record<string, string[]>;
}
