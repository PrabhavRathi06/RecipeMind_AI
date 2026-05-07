import axios from 'axios';
import type { ExtractResponse, HistoryResponse, MealPlanResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 2 min timeout for LLM calls
});

export const extractRecipe = async (url: string): Promise<ExtractResponse> => {
  const res = await api.post<ExtractResponse>('/api/extract', { url });
  return res.data;
};

export const getRecipes = async (skip = 0, limit = 50): Promise<HistoryResponse> => {
  const res = await api.get<HistoryResponse>('/api/recipes', { params: { skip, limit } });
  return res.data;
};

export const getRecipeById = async (id: number): Promise<ExtractResponse> => {
  const res = await api.get<ExtractResponse>(`/api/recipes/${id}`);
  return res.data;
};

export const deleteRecipe = async (id: number): Promise<void> => {
  await api.delete(`/api/recipes/${id}`);
};

export const createMealPlan = async (recipeIds: number[]): Promise<MealPlanResponse> => {
  const res = await api.post<MealPlanResponse>('/api/meal-plan', { recipe_ids: recipeIds });
  return res.data;
};
