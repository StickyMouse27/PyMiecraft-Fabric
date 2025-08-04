package top.fish1000.pymcfabric;

import net.fabricmc.api.ModInitializer;
import py4j.GatewayServer;

public class PyMinecraftFabric implements ModInitializer {

	private void startPy4j() {
		GatewayServer gatewayServer = new GatewayServer(null);
		gatewayServer.start();
	}

	@Override
	public void onInitialize() {
		// This code runs as soon as Minecraft is in a mod-load-ready state.
		// However, some things (like resources) may still be uninitialized.
		// Proceed with mild caution.

		utils.LOGGER.info("Hello from pymc!");

		try {
			startPy4j();
		} catch (Exception e) {
			utils.LOGGER.error("Failed to start py4j server", e);
			return;
		}

		utils.LOGGER.info("Py4j server started successfully");
	}
}