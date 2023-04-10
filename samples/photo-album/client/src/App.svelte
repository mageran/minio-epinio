<script>
	import { onMount } from "svelte";
	import { Confirm } from "svelte-confirm";

	let photos = [];
	let fileinput;
	let photoSuffixes = ["JPG", "JPEG", "GIF", "PNG"];
	let inFocus = null;
	let timers = {};
	let deleteConfirmationText;
	let deleteConfirmationImageData;

	const isImage = (photoObject) =>
		photoSuffixes.some((suffix) => {
			const name = photoObject.Key;
			let index = name.lastIndexOf(".");
			if (name.length < suffix.length || index <= 0) {
				return false;
			}
			let nameSuffix = name.substr(index + 1);
			return [suffix.toUpperCase(), suffix.toLowerCase()].includes(
				nameSuffix
			);
		});

	const base64Encode = (bytes) => {
		return btoa(bytes);
	};

	const reloadBucketPhotos = async () => {
		const res = await fetch("./api/object");
		const { data } = await res.json();
		photos = data.filter(isImage);
	};

	onMount(reloadBucketPhotos);

	const onFileSelected = (e) => {
		console.log(e.target);
		let image = e.target.files[0];
		let reader = new FileReader();
		reader.readAsBinaryString(image);
		reader.onload = async (e) => {
			let url = `./api/object/${image.name}`;
			let data = base64Encode(e.target.result);
			//console.log(`encoded data: ${data}`)
			try {
				const res = await fetch(url, {
					method: "POST",
					body: data,
				});
				const obj = await res.json();
				reloadBucketPhotos();
			} catch (e) {
				console.error("Error while posting image data: %o", e);
			}
		};
	};

	const deleteImage = (photo) => async (event) => {
		console.log(`deleteImage: ${photo.Key}`);
		const url = `./api/object/${photo.Key}`;
		const method = "DELETE";
		const res = await fetch(url, { method });
		reloadBucketPhotos();
	};
</script>

<svelte:head>
	<title>Epinio Minio Access Test App</title>
	<meta name="robots" content="noindex nofollow" />
	<html lang="en" />
</svelte:head>

<main>
	<Confirm confirmTitle="Delete" cancelTitle="Cancel" let:confirm={confirm1}>
		<h1>Photo Album</h1>
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<div
			class="button"
			on:click={() => {
				fileinput.click();
			}}
		>
			Upload an image
		</div>
		<div class="photos">
			{#each photos as photo, index}
				<figure>
					{#await fetch(`./api/object/${photo.Key}`)}
						{#if photo.Metadata.Image}
							{@const width = photo.Metadata.Image.Width}
							{@const height = photo.Metadata.Image.Height}
							<div
								class="loading-placeholder"
								style="aspect-ratio: {width}/{height}"
							/>
						{:else}
							<div class="loading-placeholder">
								loading image...
							</div>
						{/if}
					{:then response}
						{#await response.text() then data}
							<div class="image-container">
								<!-- svelte-ignore a11y-click-events-have-key-events -->
								<img
									src="data:image/*;base64,{data}"
									alt="example"
									on:mouseenter={() => {
										let tkey = `k${index}`;
										try {
											clearTimeout(timers[tkey]);
										} catch (ignored) {}
										inFocus = photo;
									}}
									on:mouseleave={() => {
										let tkey = `k${index}`;
										timers[tkey] = setTimeout(() => {
											if (inFocus === photo) {
												inFocus = null;
											}
										}, 3000);
									}}
								/>
								{#if inFocus === photo}
									<!-- svelte-ignore a11y-click-events-have-key-events -->

									<svg
										style="width:24px;height:24px"
										viewBox="0 0 24 24"
										class="delete-icon delete delete-button-overlay button"
										on:click={() => {
											let tkey = `k{index}`;
											deleteConfirmationText = `Delete this image?`;
											deleteConfirmationImageData = data;
											clearTimeout(timers[tkey]);
											confirm1(deleteImage(photo));
										}}
									>
										<path
											fill="hsl(200, 40%, 20%)"
											d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"
										/>
									</svg>
								{/if}
							</div>
						{/await}
					{/await}
					<figcaption>{photo.Key}</figcaption>
				</figure>
			{/each}
		</div>
		{#if photos.length === 0}
			<h2>No Images found in your bucket.</h2>
			<h2>Use the Upload button above to change that.</h2>
		{/if}
		<input
			style="display:none"
			type="file"
			accept=".jpg, .jpeg, .png"
			on:change={(e) => onFileSelected(e)}
			bind:this={fileinput}
		/>
		<div slot="title" style="text-align:center">
			<div style="margin-bottom: 15px">
				{#if deleteConfirmationText}
					{deleteConfirmationText}
				{:else}
					Delete this image?
				{/if}
			</div>
			{#if deleteConfirmationImageData}
				<div>
					<img
						class="image-thumbnail"
						src="data:image/*;base64,{deleteConfirmationImageData}"
						alt="thumbnail"
					/>
				</div>
			{/if}
		</div>
		<span slot="description" />
	</Confirm>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	h2 {
		color: #2e0cb4;
		text-transform: capitalize;
		font-size: 3em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
	.photos {
		width: 100%;
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		grid-gap: 8px;
	}

	.button {
		padding: 10px;
		cursor: pointer;
		border: 1px solid grey;
		background-color: burlywood;
		border-radius: 8px;
		margin-bottom: 20px;
		display: inline-block;
	}

	figure,
	img,
	.loading-placeholder {
		/* add img */
		width: 100%;
		margin: 0;
		border-radius: 10px;
	}

	.loading-placeholder {
		border: 1px dashed lightblue;
		background-color: azure;
	}

	.image-container {
		position: relative;
	}

	.image-thumbnail {
		max-width: 80px;
	}

	.delete-button-overlay {
		position: absolute;
		top: 2px;
		right: 2px;
	}
</style>
