import http.server
import json
import threading
import webbrowser
from urllib.parse import urlparse

import folium
from branca.element import MacroElement
from jinja2 import Template
from skyfield.api import EarthSatellite, load, wgs84


PORT = 8000

LINE1 = (
    "1 25544U 98067A   26295.53982885  .00015507  "
    "00000-0  28373-3 0  9990"
)
LINE2 = (
    "2 25544  51.6402 331.1396 0005470 300.9161 "
    "143.1956 15.49520448591871"
)

TS = load.timescale()
SATELLITE = EarthSatellite(LINE1, LINE2, "ISS (ZARYA)", TS)


def get_iss_position():
    t = TS.now()
    geocentric = SATELLITE.at(t)
    subpoint = wgs84.subpoint(geocentric)

    return {
        "lat": float(subpoint.latitude.degrees),
        "lon": float(subpoint.longitude.degrees),
        "alt": float(subpoint.elevation.km),
        "updated": t.utc_strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


class LiveISSUpdates(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
        (function () {
            const map = {{ this.map_name }};
            const marker = {{ this.marker_name }};

            async function updateISS() {
                try {
                    const response = await fetch("/iss-position", {
                        cache: "no-store"
                    });

                    if (!response.ok) {
                        throw new Error(
                            "Position request failed: " + response.status
                        );
                    }

                    const data = await response.json();
                    const position = [data.lat, data.lon];

                    marker.setLatLng(position);

                    marker.setPopupContent(
                        "<b>ISS Location</b><br>" +
                        "Latitude: " + data.lat.toFixed(4) + "<br>" +
                        "Longitude: " + data.lon.toFixed(4) + "<br>" +
                        "Altitude: " + data.alt.toFixed(2) + " km<br>" +
                        "Updated: " + data.updated
                    );

                    map.panTo(position, {animate: true});

                } catch (error) {
                    console.error("ISS update failed:", error);
                } finally {
                    setTimeout(updateISS, 3000);
                }
            }

            updateISS();
        })();
        {% endmacro %}
    """)

    def __init__(self, map_name, marker_name):
        super().__init__()
        self._name = "LiveISSUpdates"
        self.map_name = map_name
        self.marker_name = marker_name


def generate_map():
    position = get_iss_position()

    iss_map = folium.Map(
        location=[position["lat"], position["lon"]],
        zoom_start=3,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    marker = folium.Marker(
        location=[position["lat"], position["lon"]],
        popup=folium.Popup(
            "Loading position...",
            max_width=320,
        ),
        tooltip="International Space Station",
        icon=folium.Icon(
            color="purple",
            icon="rocket",
            prefix="fa",
        ),
    ).add_to(iss_map)

    LiveISSUpdates(
        map_name=iss_map.get_name(),
        marker_name=marker.get_name(),
    ).add_to(iss_map)

    return iss_map.get_root().render().encode("utf-8")


class TrackerHandler(http.server.BaseHTTPRequestHandler):
    map_html = b""

    def send_content(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            self.send_content(
                200,
                "text/html; charset=utf-8",
                self.map_html,
            )

        elif path == "/iss-position":
            try:
                body = json.dumps(
                    get_iss_position(),
                    allow_nan=False,
                ).encode("utf-8")

                self.send_content(
                    200,
                    "application/json; charset=utf-8",
                    body,
                )

            except Exception as error:
                print(f"Position error: {error}")

                self.send_content(
                    500,
                    "application/json",
                    b'{"error": "Could not calculate ISS position"}',
                )

        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    TrackerHandler.map_html = generate_map()

    with http.server.HTTPServer(
        ("127.0.0.1", PORT),
        TrackerHandler,
    ) as server:
        url = f"http://localhost:{PORT}"

        print(f"Server running at {url}")
        print("Press Ctrl+C to stop.")

        threading.Timer(
            0.5,
            lambda: webbrowser.open(url),
        ).start()

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")