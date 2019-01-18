-- Classement des ventes par pizzeria

SELECT piz.name pizzeria_name, item.name item_name, count(t_o.id) nb_sells
FROM pizzeria piz JOIN taken_order t_o ON piz.id = t_o.pizzeria_id
JOIN contains_item c_i ON t_o.id = c_i.order_id
JOIN catalog_item item ON c_i.item_id = item.id
GROUP BY pizzeria_name, item_name ORDER BY pizzeria_name, nb_sells DESC;


-- Nombre de commandes non finalisées par pizzeria

SELECT piz.name pizzeria_name, count(*) nb_awaiting_orders
FROM pizzeria piz JOIN taken_order t_o ON piz.id = t_o.pizzeria_id
JOIN contains_item c_i ON t_o.id = c_i.order_id
JOIN catalog_item item ON c_i.item_id = item.id
JOIN order_status o_s ON t_o.status_id = o_s.id
WHERE o_s.label IN ('En cours', 'En attente')
GROUP BY pizzeria_name ORDER BY nb_awaiting_orders DESC;

-- Nom, prénom, adresse des employés gestionnaires d'OC Pizza

SELECT piz.name pizzeria_name, m.name employee_name, m.firstname employee_firstname,
add.home_number || ', ' || add.street_name || '(' || add.zip_code || ')' street
FROM pizzeria piz JOIN member m ON piz.id = m.works_at_pizzeria_id
JOIN address add ON m.address_id = add.id
JOIN role r ON m.role_id = r.id
WHERE r.name = 'Gestionnaire'
ORDER BY pizzeria_name, employee_name, employee_firstname;

-- Recettes possibles à préparer par pizzeria (stock disponible)

SELECT piz.name pizzeria_name, recipe.name recipe_name
FROM pizzeria piz JOIN has_product_in_stock has_pro ON piz.id = has_pro.pizzeria_id
JOIN product pro ON has_pro.product_id = pro.id
JOIN requires_product req_pro ON pro.id = req_pro.product_id
JOIN recipe ON req_pro.recipe_id = recipe.id
WHERE req_pro.gram_amount <= pro.gram_weight
GROUP BY pizzeria_name, recipe_name;
