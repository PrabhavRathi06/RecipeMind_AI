import { useState, useEffect, useCallback } from 'react';
import { getRecipes, getRecipeById, deleteRecipe, createMealPlan } from '../api/client';
import type { RecipeListItem, RecipeDetail, MealPlanResponse } from '../types';
import RecipeModal from './RecipeModal';

export default function HistoryTab() {
  const [recipes, setRecipes] = useState<RecipeListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecipe, setSelectedRecipe] = useState<RecipeDetail | null>(null);
  const [modalLoading, setModalLoading] = useState(false);

  // meal planner state
  const [planIds, setPlanIds] = useState<number[]>([]);
  const [planLoading, setPlanLoading] = useState(false);
  const [mealPlan, setMealPlan] = useState<MealPlanResponse | null>(null);
  const [planError, setPlanError] = useState<string | null>(null);

  const fetchRecipes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getRecipes();
      setRecipes(res.recipes);
      setTotal(res.total);
    } catch {
      setError('Failed to load recipe history.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchRecipes(); }, [fetchRecipes]);

  const openModal = async (id: number) => {
    setModalLoading(true);
    try {
      const res = await getRecipeById(id);
      if (res.recipe) setSelectedRecipe(res.recipe);
    } catch {
      alert('Failed to load recipe details.');
    } finally {
      setModalLoading(false);
    }
  };

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`Delete "${title}"?`)) return;
    try {
      await deleteRecipe(id);
      setRecipes(prev => prev.filter(r => r.id !== id));
      setTotal(prev => prev - 1);
      setPlanIds(prev => prev.filter(pid => pid !== id));
    } catch {
      alert('Failed to delete recipe.');
    }
  };

  const togglePlanSelect = (id: number) => {
    setPlanIds(prev =>
      prev.includes(id) ? prev.filter(p => p !== id) : prev.length < 5 ? [...prev, id] : prev
    );
    setMealPlan(null);
  };

  const handleGeneratePlan = async () => {
    if (planIds.length < 2) return;
    setPlanLoading(true);
    setPlanError(null);
    try {
      const res = await createMealPlan(planIds);
      setMealPlan(res);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setPlanError(msg || 'Failed to generate meal plan.');
    } finally {
      setPlanLoading(false);
    }
  };

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const getDiffClass = (d: string | null) => d ? `difficulty-badge difficulty-${d.toLowerCase()}` : '';

  return (
    <div>
      <div className="history-header">
        <div>
          <div className="history-title">Recipe History</div>
          <div className="history-count">{total} recipe{total !== 1 ? 's' : ''} saved</div>
        </div>
        <button
          id="refresh-history-btn"
          onClick={fetchRecipes}
          style={{ padding: '0.5rem 1rem', background: 'var(--glass)', border: '1px solid var(--border)', color: 'var(--text-secondary)', borderRadius: 'var(--radius-xs)', cursor: 'pointer', fontFamily: 'Inter, sans-serif', fontSize: '0.85rem' }}
        >
          Refresh
        </button>
      </div>

      {/* meal planner bar */}
      {recipes.length >= 2 && (
        <div className="meal-planner-bar">
          <span className="meal-planner-title">Meal Planner</span>
          <span className="meal-planner-selected">
            {planIds.length === 0
              ? 'Select 2–5 recipes to generate a combined shopping list'
              : `${planIds.length} recipe${planIds.length > 1 ? 's' : ''} selected`}
          </span>
          {planIds.length > 0 && (
            <button className="btn-clear-plan" onClick={() => { setPlanIds([]); setMealPlan(null); }}>Clear</button>
          )}
          <button
            id="generate-meal-plan-btn"
            className="btn-generate-plan"
            disabled={planIds.length < 2 || planLoading}
            onClick={handleGeneratePlan}
          >
            {planLoading ? 'Generating...' : 'Generate Plan'}
          </button>
        </div>
      )}

      {planError && <div className="status-message error" style={{ marginBottom: '1rem' }}><span className="icon-warning">!</span> {planError}</div>}

      {/* meal plan result */}
      {mealPlan && (
        <div className="meal-plan-result">
          <h3>Combined Shopping List</h3>
          <div className="selected-recipe-tags">
            {mealPlan.recipe_titles.map((t, i) => <span key={i} className="selected-tag">{t}</span>)}
          </div>
          <div className="meal-plan-categories">
            {Object.entries(mealPlan.combined_shopping_list).filter(([, items]) => items.length > 0).map(([cat, items]) => (
              <div key={cat} className="meal-plan-category">
                <h4>{cat}</h4>
                <ul>{items.map((item, i) => <li key={i}>{item}</li>)}</ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* data table */}
      {error && <div className="status-message error"><span className="icon-warning">!</span> {error}</div>}

      {loading ? (
        <div className="loading-container"><div className="spinner" /><p style={{ color: 'var(--text-secondary)' }}>Loading history…</p></div>
      ) : recipes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📄</div>
          <p>No recipes extracted yet.<br />Go to Extract Recipe tab to get started!</p>
        </div>
      ) : (
        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Recipe</th>
                <th>Cuisine</th>
                <th>Difficulty</th>
                <th>Date Extracted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {recipes.map(r => (
                <tr key={r.id}>
                  <td>
                    <div style={{ fontWeight: 500 }}>{r.title || 'Untitled'}</div>
                    <div className="recipe-url-cell">{r.url}</div>
                  </td>
                  <td>{r.cuisine || '—'}</td>
                  <td>{r.difficulty ? <span className={getDiffClass(r.difficulty)}>{r.difficulty}</span> : '—'}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{formatDate(r.created_at)}</td>
                  <td>
                    <div className="table-actions">
                      <button
                        className={`btn-plan-select ${planIds.includes(r.id) ? 'selected' : ''}`}
                        onClick={() => togglePlanSelect(r.id)}
                        title="Add to meal plan"
                      >
                        {planIds.includes(r.id) ? '✓' : '+'} Plan
                      </button>
                      <button
                        id={`details-btn-${r.id}`}
                        className="btn-details"
                        onClick={() => openModal(r.id)}
                        disabled={modalLoading}
                      >
                        Details
                      </button>
                      <button
                        id={`delete-btn-${r.id}`}
                        className="btn-delete"
                        onClick={() => handleDelete(r.id, r.title || 'this recipe')}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedRecipe && (
        <RecipeModal recipe={selectedRecipe} onClose={() => setSelectedRecipe(null)} />
      )}
    </div>
  );
}
