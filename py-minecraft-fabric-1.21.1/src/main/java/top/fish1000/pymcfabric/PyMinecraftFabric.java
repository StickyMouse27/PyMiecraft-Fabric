package top.fish1000.pymcfabric;

import net.fabricmc.api.ModInitializer;

public class PyMinecraftFabric implements ModInitializer {

	@Override
	public void onInitialize() {
		// This code runs as soon as Minecraft is in a mod-load-ready state.
		// However, some things (like resources) may still be uninitialized.
		// Proceed with mild caution.

		PymcMngr.LOGGER.info("Hello from pymc!");
	}
}