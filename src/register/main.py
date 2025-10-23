from bd import register_player, login_player, show_all_players
from bd import add_score, show_scores

db_path = "./src/register/GalactaDB.db"

nuevo_jugador = {
    "username": "Jugador_Estrella",
    "full_name": "Maria Rodríguez",
    "email": "noemivargas2902@gmail.com",
    "password": "seguro",
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
#show_scores("player2")

# Mostrar jugadores guardados
show_all_players()

