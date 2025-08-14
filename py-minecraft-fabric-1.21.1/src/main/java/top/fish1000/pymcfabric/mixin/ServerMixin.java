package top.fish1000.pymcfabric.mixin;

import net.minecraft.server.MinecraftServer;
import net.minecraft.util.profiler.Profiler;

import py4j.GatewayServer;

import top.fish1000.pymcfabric.PymcMngr;
import top.fish1000.pymcfabric.executor.NamedAdvancedExecutor;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(MinecraftServer.class)
public abstract class ServerMixin {

    @Shadow
    public Profiler profiler;

    private GatewayServer startPy4j() {
        GatewayServer gatewayServer = new GatewayServer(new PymcMngr());
        gatewayServer.start();
        return gatewayServer;
    }

    @Inject(at = @At("HEAD"), method = "loadWorld()V")
    private void init(CallbackInfo info) {
        try {
            PymcMngr.server = (MinecraftServer) (Object) this;
            PymcMngr.gatewayServer = startPy4j();
            PymcMngr.py4jStarted = true;

            PymcMngr.executor = new NamedAdvancedExecutor<>(PymcMngr.server::getTicks);
        } catch (Exception e) {
            PymcMngr.LOGGER.error("Failed to start py4j server", e);
            return;
        }
        PymcMngr.LOGGER.info("Py4j server started successfully");
    }

    @Inject(at = @At(value = "INVOKE", target = "Lnet/minecraft/server/function/CommandFunctionManager;tick()V", shift = At.Shift.AFTER), method = "tickWorlds")
    private void tick(CallbackInfo info) {
        profiler.swap("py4j");
        // long start = System.nanoTime();
        PymcMngr.tick("tick");
        // long end = System.nanoTime();
        // utils.LOGGER.info("py4j tick: {}ms", (end - start) / 1000000d);
    }
}
