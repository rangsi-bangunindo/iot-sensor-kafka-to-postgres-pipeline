def enrich_sensor_data(sensor_data, metadata_dict):
    device_id = sensor_data.get("device_id")
    enrichment = metadata_dict.get(device_id)

    if enrichment is None:
        enrichment = {
            "device_name": "Perangkat Tidak Dikenal",
            "location": "Lokasi Tidak Diketahui",
            "manufacturer": "Tidak Diketahui"
        }

    enriched_data = {
        **sensor_data,
        **enrichment
    }
    return enriched_data
