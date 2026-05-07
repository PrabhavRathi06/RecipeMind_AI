import type { RecipeDetail } from '../types';
import RecipeDisplay from './RecipeDisplay';

interface Props {
  recipe: RecipeDetail;
  onClose: () => void;
}

export default function RecipeModal({ recipe, onClose }: Props) {
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h2>{recipe.title || 'Recipe Details'}</h2>
          <button id="modal-close-btn" className="modal-close" onClick={onClose} aria-label="Close modal">✕</button>
        </div>
        <div className="modal-body">
          <RecipeDisplay recipe={recipe} />
        </div>
      </div>
    </div>
  );
}
