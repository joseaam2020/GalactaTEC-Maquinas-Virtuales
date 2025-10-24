from bd import register_player, login_player, show_all_players
from bd import add_score, show_scores

from register.bd import register_player

db_path = "./src/register/GalactaDB.db"

nuevo_jugador = {
    "username": "player2",
    "full_name": "Carlos Rodríguez",
    "email": "carlos@example.com",
    "password": "1234seguro",
    "photo_path": "./resources/imgs/avatar2.png",
    "ship_image": "blue_ship.png",
    "music_pref": "Rock"
}

if register_player(
    nuevo_jugador["username"],
    nuevo_jugador["full_name"],
    nuevo_jugador["email"],
    nuevo_jugador["password"],
    nuevo_jugador["photo_path"],
    nuevo_jugador["ship_image"],
    nuevo_jugador["music_pref"],
    db_path
):
    print("Jugador agregado correctamente.")
else:
    print("Error al agregar el jugador.")



# Mostrar puntajes de ese jugador
show_scores("noemi_gamer")

# Mostrar jugadores guardados
show_all_players()

