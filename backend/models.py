from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, nullable=False, index=True)
    title = Column(String(512), nullable=True)
    cuisine = Column(String(128), nullable=True)
    difficulty = Column(String(64), nullable=True)
    prep_time = Column(String(64), nullable=True)
    cook_time = Column(String(64), nullable=True)
    total_time = Column(String(64), nullable=True)
    servings = Column(String(64), nullable=True)
    raw_html = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    instructions = relationship("Instruction", back_populates="recipe", cascade="all, delete-orphan", order_by="Instruction.step_number")
    nutrition = relationship("Nutrition", back_populates="recipe", uselist=False, cascade="all, delete-orphan")
    substitutions = relationship("Substitution", back_populates="recipe", cascade="all, delete-orphan")
    shopping_list = relationship("ShoppingListItem", back_populates="recipe", cascade="all, delete-orphan")
    related_recipes = relationship("RelatedRecipe", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    quantity = Column(String(64), nullable=True)
    unit = Column(String(64), nullable=True)
    item = Column(String(256), nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")


class Instruction(Base):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    instruction_text = Column(Text, nullable=False)

    recipe = relationship("Recipe", back_populates="instructions")


class Nutrition(Base):
    __tablename__ = "nutrition"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, unique=True)
    calories = Column(String(64), nullable=True)
    protein = Column(String(64), nullable=True)
    carbs = Column(String(64), nullable=True)
    fat = Column(String(64), nullable=True)

    recipe = relationship("Recipe", back_populates="nutrition")


class Substitution(Base):
    __tablename__ = "substitutions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    original = Column(String(256), nullable=False)
    replacement = Column(String(256), nullable=False)
    reason = Column(String(512), nullable=True)

    recipe = relationship("Recipe", back_populates="substitutions")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    category = Column(String(128), nullable=False)
    item = Column(String(256), nullable=False)

    recipe = relationship("Recipe", back_populates="shopping_list")


class RelatedRecipe(Base):
    __tablename__ = "related_recipes"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(String(1024), nullable=True)
    suggested_url = Column(String(2048), nullable=True)

    recipe = relationship("Recipe", back_populates="related_recipes")
