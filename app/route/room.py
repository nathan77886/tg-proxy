from app import app


@app.route('/room/create')
async def create_room(request):
    """Create a new room."""
    return {}