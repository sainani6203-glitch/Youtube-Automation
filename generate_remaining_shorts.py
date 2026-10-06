from run_daily_batch import run_pipeline

long_url = 'https://youtu.be/Ou9KolSHeWI'
topic = 'Dark Psychology'
angles = ['shocking_fact', 'hidden_truth', 'unsolved_mystery', 'bizarre_experiment', 'deep_paradox']

for angle in angles:
    print(f"\n==================================================")
    print(f"🚀 Generating Short with angle: {angle}")
    print(f"==================================================")
    try:
        run_pipeline(
            video_type='short',
            custom_topic=topic,
            linked_long_video_url=long_url,
            short_angle=angle
        )
        print(f"[Success] Short finished for angle: {angle}")
    except Exception as e:
        print(f"[Error] Failed for angle {angle}: {e}")
