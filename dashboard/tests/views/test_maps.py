import datetime

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

import mapbox_vector_tile
from django.utils import timezone

from dashboard.models import Occurrence, Species, DataImport, Dataset


class VectorTilesServerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_species = Species.objects.all()[0]
        cls.second_species = Species.objects.all()[1]

        cls.di = DataImport.objects.create(start=timezone.now())
        cls.first_dataset = Dataset.objects.create(
            name="Test dataset", gbif_id="4fa7b334-ce0d-4e88-aaae-2e0c138d049e"
        )
        cls.second_dataset = Dataset.objects.create(
            name="Test dataset #2", gbif_id="aaa7b334-ce0d-4e88-aaae-2e0c138d049f"
        )

        Occurrence.objects.create(
            gbif_id=1,
            species=cls.first_species,
            date=datetime.date.today(),
            data_import=cls.di,
            source_dataset=cls.first_dataset,
            location=Point(5.09513, 50.48941, srid=4326),  # Andenne
        )
        Occurrence.objects.create(
            gbif_id=2,
            species=cls.second_species,
            date=datetime.date.today(),
            data_import=cls.di,
            source_dataset=cls.second_dataset,
            location=Point(4.35978, 50.64728, srid=4326),  # Lillois
        )

    def test_base_mvt_server(self):
        """There's a tile server returning the appropriate MIME type"""
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 1, "x": 1, "y": 1},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"], "application/vnd.mapbox-vector-tile"
        )

    def test_tiles_null_filters_ignored(self):
        """Regression test: filters at null in the URL don't create problems, the filter is just ignored.

        Derived from test_basic_data_in_hexagons()
        """
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 2, "x": 2, "y": 1},
        )
        url_with_params = f"{base_url}?startDate=null&endDate=null"
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)

        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        the_feature = decoded_tile["default"]["features"][0]
        self.assertEqual(
            the_feature["properties"]["count"], 2
        )  # It has a "count" property with the value 2

    def test_tiles_species_filter(self):
        # Multiple cases where only the occurrence in Andenne is visible

        # Case 1: Large-scale view: a single hex over Wallonia, but count = 1
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 2, "x": 2, "y": 1},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        the_feature = decoded_tile["default"]["features"][0]
        self.assertEqual(
            the_feature["properties"]["count"], 1
        )  # Only one occurrence this time, due to the filter

        # Case 2: A tile that covers an important part of Wallonia, including Andenne and Braine. Should have a single
        # polygon this time
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 8, "x": 131, "y": 86},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # Case 3: A zoomed tile with just Andenne and the close neighborhood, the hex should still be there
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 10, "x": 526, "y": 345},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # Case 4: A zoomed time on Lillois, should be empty because of the filtering
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 17, "x": 67123, "y": 44083},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

    def test_tiles_multiple_dataset_filters(self):
        """Explicitely requesting all datasets give the same results than no filtering"""
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 2, "x": 2, "y": 1},
        )
        url_with_params = f"{base_url}?&datasetsIds[]={VectorTilesServerTests.first_dataset.pk}&datasetsIds[]={VectorTilesServerTests.second_dataset.pk}"
        response = self.client.get(url_with_params)
        decoded_tile_explicit_filters = mapbox_vector_tile.decode(response.content)

        response = self.client.get(base_url)
        decoded_tile_no_filters = mapbox_vector_tile.decode(response.content)

        self.assertEqual(decoded_tile_no_filters, decoded_tile_explicit_filters)

    def test_tiles_dataset_filter(self):
        # Inspired by test_tiles_species_filter

        # Multiple cases where only the occurrence in Andenne is visible
        # (because we only ask for a the first dataset)

        # Case 1: Large-scale view: a single hex over Wallonia, but count = 1
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 2, "x": 2, "y": 1},
        )
        url_with_params = (
            f"{base_url}?&datasetsIds[]={VectorTilesServerTests.first_dataset.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        the_feature = decoded_tile["default"]["features"][0]
        self.assertEqual(
            the_feature["properties"]["count"], 1
        )  # Only one occurrence this time, due to the filter

        # Case 2: A tile that covers an important part of Wallonia, including Andenne and Braine. Should have a single
        # polygon this time
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 8, "x": 131, "y": 86},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # Case 3: A zoomed tile with just Andenne and the close neighborhood, the hex should still be there
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 10, "x": 526, "y": 345},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # Case 4: A zoomed time on Lillois, should be empty because of the filtering
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 17, "x": 67123, "y": 44083},
        )
        url_with_params = (
            f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}"
        )
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

    def test_tiles_species_multiple_species_filters(self):
        # Test based on test_tiles_species_filter(self), but with two species explicitly requested

        # We need first to add a new species and related occurrences:
        species_tetraodon = Species.objects.create(
            name="Tetraodon fluviatilis",
            gbif_taxon_key=5213564,
            group="PL",
            category="E",
        )
        Occurrence.objects.create(
            gbif_id=1000,
            species=species_tetraodon,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(4.35978, 50.64728, srid=4326),  # Lillois
        )
        Occurrence.objects.create(
            gbif_id=1001,
            species=species_tetraodon,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(4.35978, 50.64728, srid=4326),  # Lillois
        )
        Occurrence.objects.create(
            gbif_id=1002,
            species=species_tetraodon,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(4.35978, 50.64728, srid=4326),  # Lillois
        )

        # Case 1: Large-scale view: a single hex over Wallonia
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 2, "x": 2, "y": 1},
        )
        url_with_params = f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}&speciesIds[]={species_tetraodon.pk}"
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        the_feature = decoded_tile["default"]["features"][0]
        self.assertEqual(
            the_feature["properties"]["count"], 4
        )  # 3 in Lillois (tetraodon, 1 in Andenne)

        # Case 2: A tile that covers an important part of Wallonia, including Andenne and Lillois. Should have two polygons
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 8, "x": 131, "y": 86},
        )
        url_with_params = f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}&speciesIds[]={species_tetraodon.pk}"
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(len(decoded_tile["default"]["features"]), 2)

        # We should have one occurrence in Andenne (for first species) and 3 in Lillois (for tetraodon)
        pass
        for entry in decoded_tile["default"]["features"]:
            self.assertIn(entry["properties"]["count"], [1, 3])

        # Case 3: A zoomed tile with just Andenne and the close neighborhood, the hex should still be there
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 10, "x": 526, "y": 345},
        )
        url_with_params = f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}&speciesIds[]={species_tetraodon.pk}"
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # Case 4: A zoomed time on Lillois, we expect the three tetraodon occurrences
        base_url = reverse(
            "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
            kwargs={"zoom": 17, "x": 67123, "y": 44083},
        )
        url_with_params = f"{base_url}?speciesIds[]={VectorTilesServerTests.first_species.pk}&speciesIds[]={species_tetraodon.pk}"
        response = self.client.get(url_with_params)
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 3
        )

    def test_tiles_basic_data_in_hexagons(self):
        # Very large view (big part of Europe, Africa and Russia: e expect a single hexagon over Belgium
        #
        # Those tests can be more easily debugged with a "TileDebug" layer in OpenLayers:
        # https://openlayers.org/en/latest/examples/canvas-tiles.html
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 2, "x": 2, "y": 1},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)

        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        the_feature = decoded_tile["default"]["features"][0]
        self.assertEqual(
            the_feature["properties"]["count"], 2
        )  # It has a "count" property with the value 2
        self.assertEqual(
            the_feature["geometry"]["type"], "Polygon"
        )  # the feature is a polygon
        self.assertEqual(
            len(the_feature["geometry"]["coordinates"][0]), 7
        )  # 7 coordinates pair = 6 sides

        # Another very large tile, over Groenland. Should be empty
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 2, "x": 1, "y": 0},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

        # A tile that covers an important part of Wallonia, including Andenne and Braine. Should have two polygons
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 8, "x": 131, "y": 86},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 2
        )  # it has two features

        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )
        self.assertEqual(
            decoded_tile["default"]["features"][1]["properties"]["count"], 1
        )

        # The tile east of it should be empty
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 8, "x": 132, "y": 86},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

        # A tile with just Andenne and the close neighborhood
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 10, "x": 526, "y": 345},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # The one on the west is empty
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 10, "x": 525, "y": 345},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

        # Let's get a very small tile containing the Lillois occurrence
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 17, "x": 67123, "y": 44083},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(
            len(decoded_tile["default"]["features"]), 1
        )  # it has a single feature
        self.assertEqual(
            decoded_tile["default"]["features"][0]["properties"]["count"], 1
        )

        # The next one is empty
        response = self.client.get(
            reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 17, "x": 67124, "y": 44083},
            )
        )
        decoded_tile = mapbox_vector_tile.decode(response.content)
        self.assertEqual(decoded_tile, {})

    def test_zoom_levels(self):
        """Zoom levels 1-20 are supported"""
        for zoom_level in range(1, 21):
            response = self.client.get(
                reverse(
                    "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                    kwargs={"zoom": zoom_level, "x": 1, "y": 1},
                )
            )
            self.assertEqual(response.status_code, 200)
            mapbox_vector_tile.decode(response.content)

    def test_min_max_per_hexagon(self):
        # At zoom level 8, with the initial data: we should have two polygons, both at 1. So min=1 and max=1
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"), data={"zoom": 8}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 1)

        # Add a second one in Lillois, but not next to the other one
        Occurrence.objects.create(
            gbif_id=3,
            species=Species.objects.all()[0],
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(4.36229, 50.64628, srid=4326),  # Lillois, bakkerij
        )

        # Now, at zoom level 8 we should have an hexagon with count=1 and another one with count=2
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"), data={"zoom": 8}
        )
        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 2)

        # But at a very large scale, one single hexagon with count=3
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"), data={"zoom": 1}
        )
        self.assertEqual(response.json()["min"], 3)
        self.assertEqual(response.json()["max"], 3)

        # At zoom level 17, there's no hexagons that cover more than 1 occurrence
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"), data={"zoom": 17}
        )
        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 1)

    def test_min_max_per_hexagon_with_species_filter(self):
        # Add a second one in Lillois, but not next to the other one and another species
        Occurrence.objects.create(
            gbif_id=3,
            species=VectorTilesServerTests.second_species,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(4.36229, 50.64628, srid=4326),  # Lillois, bakkerij
        )

        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={"zoom": 8, "speciesIds[]": VectorTilesServerTests.first_species.pk},
        )
        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 1)

        # Now we're looking for the second species. (We have 2 in Lillois and none in Andenne)
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={
                "zoom": 8,
                "speciesIds[]": [VectorTilesServerTests.second_species.pk],
            },
        )

        self.assertEqual(response.json()["min"], 2)
        self.assertEqual(response.json()["max"], 2)

        # Now let's add another one in Andenne for species 2: whe should now have 1,2
        Occurrence.objects.create(
            gbif_id=4,
            species=VectorTilesServerTests.second_species,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(5.095610, 50.48800, srid=4326),
        )

        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={"zoom": 8, "speciesIds[]": VectorTilesServerTests.second_species.pk},
        )

        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 2)

    def test_min_max_per_hexagon_with_dataset_filter(self):
        # Add a second one in Lillois, but not next to the other one and another species
        Occurrence.objects.create(
            gbif_id=3,
            species=VectorTilesServerTests.second_species,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.second_dataset,
            location=Point(4.36229, 50.64628, srid=4326),  # Lillois, bakkerij
        )

        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={"zoom": 8, "datasetsIds[]": VectorTilesServerTests.first_dataset.pk},
        )
        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 1)

        # Now we're looking for the second species. (We have 2 in Lillois and none in Andenne)
        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={
                "zoom": 8,
                "speciesIds[]": [VectorTilesServerTests.second_species.pk],
            },
        )

        self.assertEqual(response.json()["min"], 2)
        self.assertEqual(response.json()["max"], 2)

        # Now let's add another one in Andenne for species 2: whe should now have 1,2
        Occurrence.objects.create(
            gbif_id=4,
            species=VectorTilesServerTests.second_species,
            date=datetime.date.today(),
            data_import=VectorTilesServerTests.di,
            source_dataset=VectorTilesServerTests.first_dataset,
            location=Point(5.095610, 50.48800, srid=4326),
        )

        response = self.client.get(
            reverse("dashboard:api-mvt-min-max-per-hexagon"),
            data={"zoom": 8, "speciesIds[]": VectorTilesServerTests.second_species.pk},
        )

        self.assertEqual(response.json()["min"], 1)
        self.assertEqual(response.json()["max"], 2)