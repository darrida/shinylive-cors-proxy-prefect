


from api_call import get_url
from pydantic import BaseModel
from shiny.express import input, render, ui


class Item(BaseModel):
    name: str
    age: int

ui.input_slider("n", "N", 0, 100, 20)

@render.text
def txt():
    return f"n*2 is {input.n() * 2}"

ui.hr()

@render.ui
async def markdwn():
    results = await get_url(
        url="http://localhost:8000/prefect-proxy/me",
        headers={"Authorization": "Bearer pnu_6CNzZ0XXJm2yscYJdghuT5OkQFhozl3UMf7q"},
        type="json",
        clone=True
    )
    status = results.status
    data = results.data
    item = Item(name="thing", age=4)
    return ui.markdown(
        f"""
        # Title
        ## Subtitle
        - bullet1
        - bullet2

        ## Subtitle 2
        ```python
        for i in list1:
            print(i)
        ```
        ## Item
        {item.name}, {item.age}

        ## API
        {status}
        {data}
        """
    )
