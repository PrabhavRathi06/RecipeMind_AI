import type { RecipeDetail } from '../types';

interface Props { recipe: RecipeDetail; }

export default function RecipeDisplay({ recipe }: Props) {
  const groupedShopping = recipe.shopping_list.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item.item);
    return acc;
  }, {} as Record<string, string[]>);

  const diffClass = recipe.difficulty
    ? `difficulty-${recipe.difficulty.toLowerCase()}`
    : 'difficulty-easy';

  return (
    <div className="recipe-display">
      {/* Header */}
      <div className="recipe-header-card">
        <div className="recipe-title">{recipe.title || 'Extracted Recipe'}</div>
        <div className="recipe-meta">
          {recipe.cuisine && <span className="meta-badge">{recipe.cuisine}</span>}
          {recipe.prep_time && <span className="meta-badge">Prep: {recipe.prep_time}</span>}
          {recipe.cook_time && <span className="meta-badge">Cook: {recipe.cook_time}</span>}
          {recipe.total_time && <span className="meta-badge">Total: {recipe.total_time}</span>}
          {recipe.servings && <span className="meta-badge">{recipe.servings}</span>}
          {recipe.difficulty && <span className={`difficulty-badge ${diffClass}`}>{recipe.difficulty}</span>}
        </div>
        <a href={recipe.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-muted)', fontSize: '0.78rem', wordBreak: 'break-all' }}>{recipe.url}</a>
      </div>

      {/* Row 1: Ingredients + Instructions */}
      <div className="recipe-grid" style={{ marginBottom: '1.5rem' }}>
        {/* Ingredients */}
        <div className="section-card">
          <div className="card-header">
            <span className="card-title">Ingredients</span>
            <span className="card-count">{recipe.ingredients.length} items</span>
          </div>
          <ul className="ingredient-list">
            {recipe.ingredients.map((ing, i) => (
              <li key={i} className="ingredient-item">
                <span className="ing-qty">{ing.quantity || '—'}</span>
                <span className="ing-unit">{ing.unit || ''}</span>
                <span className="ing-name">{ing.item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Instructions */}
        <div className="section-card">
          <div className="card-header">
            <span className="card-title">Instructions</span>
            <span className="card-count">{recipe.instructions.length} steps</span>
          </div>
          <ol className="instruction-list">
            {recipe.instructions.map((inst) => (
              <li key={inst.step_number} className="instruction-step">
                <span className="step-num">{inst.step_number}</span>
                <span className="step-text">{inst.instruction_text}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Row 2: Nutrition + Substitutions */}
      <div className="recipe-grid" style={{ marginBottom: '1.5rem' }}>
        {/* Nutrition */}
        {recipe.nutrition && (
          <div className="section-card">
            <div className="card-header">
              <span className="card-title">Nutrition Estimate</span>
              <span className="card-count">per serving</span>
            </div>
            <div className="nutrition-grid">
              {[
                { label: 'Calories', value: recipe.nutrition.calories },
                { label: 'Protein', value: recipe.nutrition.protein },
                { label: 'Carbs', value: recipe.nutrition.carbs },
                { label: 'Fat', value: recipe.nutrition.fat },
              ].map(n => (
                <div key={n.label} className="nutrition-item">
                  <span className="nutrition-value">{n.value || '—'}</span>
                  <span className="nutrition-label">{n.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Substitutions */}
        {recipe.substitutions.length > 0 && (
          <div className="section-card">
            <div className="card-header">
              <span className="card-title">Ingredient Substitutions</span>
            </div>
            <div className="sub-list">
              {recipe.substitutions.map((sub, i) => (
                <div key={i} className="sub-item">
                  <div className="sub-arrow">
                    <span className="sub-original">{sub.original}</span>
                    <span style={{ color: 'var(--text-muted)' }}>→</span>
                    <span className="sub-replacement">{sub.replacement}</span>
                  </div>
                  {sub.reason && <div className="sub-reason">Note: {sub.reason}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Row 3: Shopping List + Related Recipes */}
      <div className="recipe-grid">
        {/* Shopping List */}
        {Object.keys(groupedShopping).length > 0 && (
          <div className="section-card">
            <div className="card-header">
              <span className="card-title">Shopping List</span>
            </div>
            <div className="shopping-categories">
              {Object.entries(groupedShopping).map(([cat, items]) => (
                <div key={cat}>
                  <div className="shopping-category-name">{cat}</div>
                  <div className="shopping-items">
                    {items.map((item, i) => (
                      <span key={i} className="shopping-chip">{item}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Related Recipes */}
        {recipe.related_recipes.length > 0 && (
          <div className="section-card">
            <div className="card-header">
              <span className="card-title">You Might Also Like</span>
            </div>
            <div className="related-list">
              {recipe.related_recipes.map((rel, i) => (
                <div key={i} className="related-item">
                  <div className="related-dot" />
                  <div>
                    <div className="related-title">{rel.title}</div>
                    {rel.description && <div className="related-desc">{rel.description}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
