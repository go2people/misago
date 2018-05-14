// jshint ignore:start
import React from 'react';
import Category from './category';
import NavbarSearch from 'misago/components/navbar-search'; // jshint ignore:line

export default function({ categories }) {
  return (
    <div className="categories-list">
      {/*<NavbarSearch />*/}
      {categories.map((category) => {
        return (
          <Category
            category={category}
            key={category.id}
          />
        );
      })}
    </div>
  );
}